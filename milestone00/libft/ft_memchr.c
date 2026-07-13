/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   ft_memchr.c                                        :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: kyonaha <kyonaha@student.42tokyo.jp>       +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2026/04/24 15:44:13 by kyonaha           #+#    #+#             */
/*   Updated: 2026/04/28 16:29:52 by kyonaha          ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include "libft.h"

void	*ft_memchr(const void *src, int chr, size_t num)
{
	size_t	idx;

	idx = 0;
	while (idx < num && ((unsigned char *)src)[idx] != (unsigned char)chr)
		idx++;
	if (idx != num)
		return ((unsigned char *)src + idx);
	else
		return (NULL);
}
