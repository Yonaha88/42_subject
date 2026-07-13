/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   ft_memset.c                                        :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: kyonaha <kyonaha@student.42tokyo.jp>       +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2026/04/23 19:08:07 by kyonaha           #+#    #+#             */
/*   Updated: 2026/04/28 16:29:33 by kyonaha          ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include "libft.h"

void	*ft_memset(void *src, int chr, size_t num)
{
	size_t	idx;

	idx = 0;
	while (idx < num)
	{
		((unsigned char *)src)[idx] = (unsigned char)chr;
		idx++;
	}
	return (src);
}
