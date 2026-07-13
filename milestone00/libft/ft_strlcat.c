/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   ft_strlcat.c                                       :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: kyonaha <kyonaha@student.42tokyo.jp>       +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2026/04/24 11:36:37 by kyonaha           #+#    #+#             */
/*   Updated: 2026/04/28 16:29:03 by kyonaha          ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include "libft.h"

size_t	ft_strlcat(char *dest, const char *src, size_t size)
{
	size_t	idx;
	size_t	dest_len;

	idx = 0;
	dest_len = ft_strlen(dest);
	if (size <= dest_len)
		return (size + ft_strlen(src));
	else
	{
		while (dest_len + idx < size - 1 && src[idx] != '\0')
		{
			dest[dest_len + idx] = src[idx];
			idx++;
		}
		dest[dest_len + idx] = '\0';
		return (dest_len + ft_strlen(src));
	}
}
